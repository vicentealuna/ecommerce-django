#!/usr/bin/env bash
# Revisa que ni los commits ni los archivos nuevos traigan marcas de agua de IA.
# Uso: BASE=<commit> HEAD=<commit> bash .github/scripts/sin-marca-de-agua.sh
set -u
source "$(dirname "$0")/patrones.sh"

HEAD="${HEAD:-HEAD}"
BASE="${BASE:-}"
VACIO="4b825dc642cb6eb9a060e54bf8d69288fbee4904"   # arbol vacio de git

# Sin base valida (primer push de una rama): se revisa todo el historial.
if [ -z "$BASE" ] || ! git cat-file -e "${BASE}^{commit}" 2>/dev/null; then
  RANGO="$HEAD"
  DESDE="$VACIO"
else
  RANGO="${BASE}..${HEAD}"
  DESDE="$BASE"
fi

fallos=0

echo "== Mensajes de commit =="
for c in $(git rev-list "$RANGO"); do
  if git log -1 --format=%B "$c" | grep -iEq "$PATRON_COMMIT"; then
    echo "MARCA DE AGUA en el commit $(git log -1 --format='%h  %an  %s' "$c")"
    git log -1 --format=%B "$c" | grep -iE "$PATRON_COMMIT" | sed 's/^/      /'
    fallos=1
  fi
done

echo "== Archivos =="
# Solo lineas agregadas. No se revisan docs/ ni .github/ porque explican esta regla.
encontradas=$(git diff "$DESDE" "$HEAD" --unified=0 -- . ':(exclude)docs' ':(exclude).github' ':(exclude).githooks' \
  | grep -E '^\+' | grep -vE '^\+\+\+' | grep -iE "$PATRON_CODIGO" || true)
if [ -n "$encontradas" ]; then
  echo "MARCA DE AGUA en archivos:"
  echo "$encontradas" | sed 's/^/      /'
  fallos=1
fi

if [ "$fallos" -ne 0 ]; then
  echo
  echo "RECHAZADO. Quita las marcas de agua. Como hacerlo: docs/GUIA-GIT.md, seccion 10."
  exit 1
fi
echo "OK: sin marcas de agua."
