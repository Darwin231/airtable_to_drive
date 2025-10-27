import os
import io
import pandas as pd

from pathlib import Path
from typing import Optional, List
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import json, base64


class GPCUtils:
    def __init__(
        self,
        folder_id: Optional[str] = None,
        client_path: Optional[str] = None,
        token_path: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        quota_project: Optional[str] = None
    ):
        """
        folder_id: ID de la carpeta (incluye Shared Drives)
        client_path/token_path: rutas a client_secret.json y tokens.json
        scopes: lista de scopes para Drive
        quota_project: opcional, proyecto de cuota
        """

        workspace = os.getenv("GITHUB_WORKSPACE")
        if workspace:
            conf_dir = Path(workspace) / "conf"
        else:
            # project_root/ conf  (two levels up from CWD to be safer)
            conf_dir = Path(
                os.path.abspath(
                    os.path.join(
                        os.getcwd(), "..", "..", "conf")
                )
            )
        conf_dir.mkdir(parents=True, exist_ok=True)

        # 2) File locations (overridable)
        self.CLIENT_PATH = Path(client_path) if client_path else conf_dir / "client_secret.json"
        self.TOKEN_PATH = Path(token_path) if token_path else conf_dir / "tokens.json"


        # Para listar en Shared Drives y subir archivos:
        # - drive.metadata.readonly: listar metadatos
        # - drive.file: subir/editar archivos creados por tu app
        self.SCOPES = scopes or [
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/drive.file',
        ]
        self.folder_id = folder_id
        self.quota_project = quota_project
        self.service = None

    def auth(self):
        """
        Autenticación con prioridad:
        1. CLOUD_SECRET (Service Account en base64 desde env vars)
        2. tokens.json (flujo OAuth local)
        """

        # Intentar primero autenticación por Service Account GH actrions
        cloud_secret_b64 = os.getenv("CLOUD_SECRET")
        if cloud_secret_b64:
            try:
                sa_info = json.loads(base64.b64decode(cloud_secret_b64))
                creds = service_account.Credentials.from_service_account_info(
                    sa_info, scopes=self.SCOPES
                )
                if self.quota_project:
                    try:
                        creds = creds.with_quota_project(self.quota_project)
                    except Exception as e:
                        print(f"⚠️  No se pudo aplicar quota project: {e}")
                self.service = build("drive", "v3", credentials=creds)
                print("✅ Autenticado mediante Service Account (CLOUD_SECRET)")
                return self.service
            except Exception as e:
                print(f"⚠️  Error al usar CLOUD_SECRET: {e}")

        # tokens.json (para ejecución local)
        creds = None
        if os.path.exists(self.TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(self.TOKEN_PATH, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_PATH, self.SCOPES)
                creds = flow.run_local_server(port=0)

            if self.quota_project:
                try:
                    creds = creds.with_quota_project(self.quota_project)
                except Exception as e:
                    print(e)
                    pass

            with open(self.TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)
        print("✅ Autenticado mediante OAuth local")
        return self.service

    def list_files(self):
        """
        Lista TODOS los archivos directos dentro de self.folder_id (soporta Shared Drives).
        Devuelve lista de dicts con id, name, mimeType y webViewLink.
        """
        if self.service is None:
            self.auth()

        query = f"'{self.folder_id}' in parents and trashed = false"
        fields = "nextPageToken, files(id,name,mimeType,webViewLink)"
        files = []
        page_token = None

        while True:
            resp = self.service.files().list(
                q=query,
                fields=fields,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                pageToken=page_token
            ).execute()

            items = resp.get('files', [])
            files.extend(items)
            page_token = resp.get('nextPageToken')
            if not page_token:
                break

        # salida cómoda por consola
        if not files:
            print("📂 La carpeta está vacía o no tienes acceso.")
        else:
            print(f"✅ {len(files)} archivo(s) encontrados:")
            for f in files:
                print(f" - {f['name']} ({f['id']})")

        return files

    def upload_dataframe_xlsx(self, df: pd.DataFrame, drive_filename: str, replace_if_exists: bool = True):
        """
        Sube un DataFrame como .xlsx a self.folder_id (sin archivo local).
        Si replace_if_exists=True, actualiza el archivo si existe uno con el mismo nombre.
        """
        if self.service is None:
            self.auth()

        # 1) Excel en memoria
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='data')
        buf.seek(0)

        # 2) Buscar si existe archivo con ese nombre en la carpeta (para reemplazar)
        existing_id = None
        if replace_if_exists:
            safe_name = drive_filename.replace("'", "\\'")
            q = f"name = '{safe_name}' and '{self.folder_id}' in parents and trashed = false"
            search = self.service.files().list(
                q=q,
                fields="files(id,name)",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True
            ).execute()
            items = search.get('files', [])
            if items:
                existing_id = items[0]['id']

        media = MediaIoBaseUpload(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=True
        )

        if existing_id:
            # actualizar
            updated = self.service.files().update(
                fileId=existing_id,
                media_body=media,
                fields="id,name,webViewLink",
                supportsAllDrives=True
            ).execute()
            print(f"🔁 Actualizado: {updated['name']} → {updated['webViewLink']}")
            return updated
        else:
            # crear
            metadata = {'name': drive_filename, 'parents': [self.folder_id]}
            created = self.service.files().create(
                body=metadata,
                media_body=media,
                fields="id,name,webViewLink",
                supportsAllDrives=True
            ).execute()
            print(f"☁️ Subido: {created['name']} → {created['webViewLink']}")
            return created