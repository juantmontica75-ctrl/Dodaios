
<div align="center">

# JMXS

<p><b>El meta-agente que se sitúa por encima de todos tus agentes de programación. Habla con un único orquestador desde un solo chat mientras JMXS distribuye, supervisa y sincroniza automáticamente tareas complejas de ingeniería entre todas las CLI, IDE y agentes locales de tu entorno.</b></p>

<p>
  <a href="https://github.com/juantmontica75-ctrl/Dodaios/releases/latest"><img src="https://img.shields.io/github/v/release/juantmontica75-ctrl/Dodaios?label=release&labelColor=0A0A0A&color=FAFAFA" alt="Última versión" /></a>
  <a href="https://github.com/juantmontica75-ctrl/Dodaios/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-FAFAFA?labelColor=0A0A0A" alt="Licencia MIT" /></a>
  <a href="https://github.com/juantmontica75-ctrl/Dodaios/stargazers"><img src="https://img.shields.io/github/stars/juantmontica75-ctrl/Dodaios?labelColor=0A0A0A&color=FAFAFA&logo=github" alt="Estrellas en GitHub" /></a>
  <a href="https://discord.gg/x7USduHxbc"><img src="https://img.shields.io/badge/discord-unirse-FAFAFA?labelColor=0A0A0A&logo=discord&logoColor=white" alt="Discord" /></a>
</p>

<p>
  <a href="https://trendshift.io/repositories/91076?utm_source=repository-badge&utm_medium=badge&utm_campaign=badge-repository-91076" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/91076" alt="JMXS | Trendshift" width="250" height="55"/></a>
</p>

<p>
  <a href="#instalacion">Instalación</a> ·
  <a href="#tus-planes-y-claves">Tus planes</a> ·
  <a href="#documentacion">Documentación</a> ·
  <a href="https://github.com/juantmontica75-ctrl/Dodaios">Web / Repositorio</a> ·
  <a href="https://discord.gg/x7USduHxbc">Discord</a>
</p>

</div>

## Instalación

**macOS y Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/juantmontica75-ctrl/Dodaios/main/install/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/juantmontica75-ctrl/Dodaios/main/install/install.ps1 | iex
```

El instalador configura su propio entorno de Python, añade un comando de inicio y abre la aplicación. En el primer inicio eliges el nombre del asistente (que también será su palabra de activación), conectas un modelo de IA y seleccionas cómo quieres interactuar con él. Para tareas de programación, instala al menos un agente de código, como Claude Code o Codex, e inicia sesión.

```bash
jmxs            # Iniciar la aplicación
jmxs update     # Instalar la última versión
```

<details>
<summary>Instaladores de escritorio, pipx y servidores</summary>

<br />

Descarga el instalador correspondiente a tu sistema operativo desde la última versión:

| Windows | macOS | Linux |
| --- | --- | --- |
| [JMXS-Setup-x64.exe](https://github.com/juantmontica75-ctrl/Dodaios/releases/latest/download/JMXS-Setup-x64.exe) | [Apple Silicon](https://github.com/juantmontica75-ctrl/Dodaios/releases/latest/download/JMXS-macOS-arm64.dmg) · [Intel](https://github.com/juantmontica75-ctrl/Dodaios/releases/latest/download/JMXS-macOS-x64.dmg) | [AppImage, x86_64](https://github.com/juantmontica75-ctrl/Dodaios/releases/latest/download/JMXS-Linux-x86_64.AppImage) |

</details>
