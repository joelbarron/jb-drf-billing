# Release Process

## Prerequisitos (una sola vez)

### 1. RELEASE_BOT_TOKEN

El workflow `release-automation.yml` necesita un PAT de GitHub para poder hacer commits y push desde Actions.

1. GitHub → tu avatar → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**
2. Configuración:
   - **Resource owner:** `joelbarron`
   - **Repository access:** Only select repositories → `jb-drf-billing`
   - **Permissions → Contents:** Read and write
3. Genera el token y cópialo.
4. En el repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
   - Name: `RELEASE_BOT_TOKEN`
   - Value: el token copiado

### 2. Trusted Publishing en PyPI / TestPyPI

Permite que los workflows publiquen en PyPI sin guardar un API token.

**PyPI** (para releases estables):
- pypi.org → tu cuenta → **Publishing** → **Add a new pending publisher**

| Campo | Valor |
|-------|-------|
| PyPI project name | `jb-drf-billing` |
| Owner | `joelbarron` |
| Repository name | `jb-drf-billing` |
| Workflow name | `pypi-publish.yml` |
| Environment name | `pypi` |

**TestPyPI** (para release candidates):
- test.pypi.org → mismos pasos, workflow: `testpypi-publish.yml`, environment: *(dejar vacío)*

---

## Publicar un Release Candidate (RC)

1. En GitHub → **Actions** → **Release Automation** → **Run workflow**
2. Parámetros:
   - **Release type:** `rc`
   - **Version:** `0.1.0`
   - **RC number:** `1`
   - **Target branch:** `main`
3. El workflow bumps la versión a `0.1.0rc1`, hace commit, crea el tag `v0.1.0-rc1` y hace push.
4. El tag dispara `testpypi-publish.yml` automáticamente → publica en TestPyPI.

Instalar desde TestPyPI para probar:
```bash
pip install --index-url https://test.pypi.org/simple/ jb-drf-billing==0.1.0rc1
```

---

## Publicar un Release Estable

1. En GitHub → **Actions** → **Release Automation** → **Run workflow**
2. Parámetros:
   - **Release type:** `stable`
   - **Version:** `0.1.0`
   - **Target branch:** `main`
3. El workflow bumps la versión a `0.1.0`, hace commit, crea el tag `v0.1.0`, crea el GitHub Release.
4. El GitHub Release dispara `pypi-publish.yml` automáticamente → publica en PyPI.

---

## Flujo de workflows

```
release-automation.yml (manual)
    │
    ├── RC  → tag v*.*.*-rc* → testpypi-publish.yml → TestPyPI
    │
    └── stable → GitHub Release → pypi-publish.yml → PyPI
```

---

## CI

El workflow `ci.yml` corre automáticamente en cada push a `main` y en cada PR:
- Lint con ruff (`F`, `E9`)
- Tests con `unittest`
- Build + validación con twine

Para correr todo localmente antes de un release:
```bash
sh scripts/test_before_publish.sh
```
