#!/usr/bin/env sh
set -eu
umask 077

BACKUP_DIR="${BACKUP_DIR:-}"
CONFIRM_RESTORE="${CONFIRM_RESTORE:-}"
DATA_DIR="${DATA_DIR:-data}"
STUDIES_DIR="${STUDIES_DIR:-${DATA_DIR}/studies}"
PRE_RESTORE_ROOT="${PRE_RESTORE_ROOT:-${DATA_DIR}/pre-restore}"
restore_completed=0
services_stopped=0

wait_for_api_health() {
  attempts=12
  delay_seconds=5
  attempt=1

  while [ "${attempt}" -le "${attempts}" ]; do
    if docker compose exec -T api python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=5)" >/dev/null 2>&1; then
      return 0
    fi
    if [ "${attempt}" -lt "${attempts}" ]; then
      printf 'API todavía no está lista. Reintentando en %s segundos (%s/%s).\n' "${delay_seconds}" "${attempt}" "${attempts}" >&2
      sleep "${delay_seconds}"
    fi
    attempt=$((attempt + 1))
  done

  return 1
}

run_smoke_with_retries() {
  attempts=5
  delay_seconds=3
  attempt=1

  while [ "${attempt}" -le "${attempts}" ]; do
    if ./scripts/smoke.sh; then
      return 0
    fi
    if [ "${attempt}" -lt "${attempts}" ]; then
      printf 'Smoke falló tras el restore. Reintentando en %s segundos (%s/%s).\n' "${delay_seconds}" "${attempt}" "${attempts}" >&2
      sleep "${delay_seconds}"
    fi
    attempt=$((attempt + 1))
  done

  return 1
}

cleanup() {
  if [ "${services_stopped}" -eq 1 ] && [ "${restore_completed}" -ne 1 ]; then
    docker compose stop api worker >/dev/null 2>&1 || true
    printf 'Restore interrumpido o fallido. api y worker quedan detenidos para evitar escrituras sobre un estado potencialmente parcial.\n' >&2
  fi
}

trap cleanup EXIT
trap 'cleanup; exit 130' INT TERM

if [ -z "${BACKUP_DIR}" ]; then
  printf 'Uso: BACKUP_DIR=backups/<timestamp> CONFIRM_RESTORE=YES_I_UNDERSTAND sh ./scripts/restore.sh\n' >&2
  exit 1
fi

if [ "${CONFIRM_RESTORE}" != "YES_I_UNDERSTAND" ]; then
  printf 'Restore bloqueado. Reejecutá con CONFIRM_RESTORE=YES_I_UNDERSTAND.\n' >&2
  exit 1
fi

if [ ! -d "${BACKUP_DIR}" ]; then
  printf 'No existe el directorio de backup: %s\n' "${BACKUP_DIR}" >&2
  exit 1
fi

if [ ! -r "${BACKUP_DIR}" ] || [ ! -x "${BACKUP_DIR}" ]; then
  printf 'No se puede leer el directorio de backup: %s\n' "${BACKUP_DIR}" >&2
  printf 'Revisá propietario/permisos. Si lo creaste con sudo, no lo restaures como usuario normal sin corregir permisos.\n' >&2
  exit 1
fi

if [ ! -f "${BACKUP_DIR}/db.sql" ] || [ ! -f "${BACKUP_DIR}/studies.tar.gz" ] || [ ! -f "${BACKUP_DIR}/manifest.txt" ]; then
  printf 'Backup incompleto: se requieren db.sql, studies.tar.gz y manifest.txt.\n' >&2
  exit 1
fi

tar -tzf "${BACKUP_DIR}/studies.tar.gz" >/dev/null

backup_commit="$(sed -n 's/^git_commit=//p' "${BACKUP_DIR}/manifest.txt" | sed -n '1p')"
current_commit="$(git rev-parse --short HEAD 2>/dev/null || printf 'unknown')"

if [ -n "${backup_commit}" ] && [ "${backup_commit}" != "unknown" ] && [ "${current_commit}" != "unknown" ] && [ "${backup_commit}" != "${current_commit}" ]; then
  printf 'Aviso: el backup fue creado en git_commit=%s y el checkout actual es %s.\n' "${backup_commit}" "${current_commit}" >&2
fi

timestamp="$(date +%Y%m%d-%H%M%S)"
pre_restore_dir="${PRE_RESTORE_ROOT}/studies-${timestamp}"

printf 'Deteniendo api y worker para evitar escrituras durante el restore.\n'
docker compose stop api worker
services_stopped=1

printf 'Asegurando PostgreSQL y Redis activos.\n'
docker compose up -d postgres redis

printf 'Restaurando PostgreSQL desde %s/db.sql\n' "${BACKUP_DIR}"
{
  printf 'BEGIN;\n'
  printf 'DROP SCHEMA IF EXISTS public CASCADE;\n'
  printf 'CREATE SCHEMA public;\n'
  cat "${BACKUP_DIR}/db.sql"
  printf '\nCOMMIT;\n'
} | docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

printf 'Limpiando Redis porque la cola Celery es estado transitorio y no se restaura.\n'
docker compose exec -T redis redis-cli FLUSHALL >/dev/null

if [ -d "${STUDIES_DIR}" ]; then
  mkdir -p "${PRE_RESTORE_ROOT}"
  printf 'Moviendo %s a %s\n' "${STUDIES_DIR}" "${pre_restore_dir}"
  mv "${STUDIES_DIR}" "${pre_restore_dir}"
fi

mkdir -p "${DATA_DIR}"
printf 'Restaurando data/studies desde %s/studies.tar.gz\n' "${BACKUP_DIR}"
tar -xzf "${BACKUP_DIR}/studies.tar.gz" -C "${DATA_DIR}"

printf 'Reiniciando api y worker.\n'
docker compose up -d api worker

printf 'Esperando a que api responda internamente.\n'
wait_for_api_health

printf 'Reiniciando reverse-proxy para refrescar el upstream api.\n'
docker compose restart reverse-proxy

sleep 3

printf 'Verificando API vía reverse-proxy.\n'
run_smoke_with_retries

restore_completed=1
printf 'Restore completado y verificado.\n'
