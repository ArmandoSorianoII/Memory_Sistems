# Monitor de Sistemas de Memoria (Windows)

Aplicación en Python para monitorear en tiempo real diferentes aspectos de la memoria en Windows (RAM, memoria de intercambio, caché, etc.) utilizando una interfaz gráfica basada en gráficos de Matplotlib.

## Características

- **Monitoreo de RAM**: uso total y porcentaje de memoria utilizada.
- **Memoria de intercambio (swap/pagefile)**: uso de memoria virtual.
- **Memoria caché / standby** (en Windows) usando `ctypes` y APIs del sistema.
- **Gráficos en tiempo real** con historial de uso.
- Interfaz gráfica usando ventanas de Matplotlib.

## Requisitos

- **Sistema operativo**: Windows 10 o superior.
- **Python**: 3.12 (o versión 3.x compatible).
- **Dependencias de Python**:
  - `psutil`
  - `matplotlib`
  - `numpy`

Para instalarlas, desde la carpeta del proyecto:

```bash
python -m pip install psutil matplotlib numpy
```

(o usando `py` en lugar de `python`, según tu sistema)

## Estructura básica del proyecto

- `demo.py` → Script principal con la clase `MemoryMonitor` y la interfaz gráfica.
- `Gemini_Generated_Image_w7k7jdw7k7jdw7k7.ico` → Icono para el ejecutable (opcional).

## Cómo ejecutar el programa en modo script

1. Abre una terminal (PowerShell o CMD) en la carpeta del proyecto:

   ```bash
   cd C:\Users\gabri\Documents\GitHub\Memory_Sistems
   ```

2. Ejecuta el script:

   ```bash
   python demo.py
   ```

   (o `py demo.py`)

Se abrirá la ventana con los gráficos de monitoreo de memoria.

## Cómo generar el ejecutable (.exe) con PyInstaller

### 1. Instalar PyInstaller

Desde la carpeta del proyecto:

```bash
python -m pip install pyinstaller
```

### 2. Generar el ejecutable sin icono (opcional)

Para probar primero sin icono:

```bash
python -m PyInstaller --onefile --windowed --name MonitorMemoria demo.py
```

- El ejecutable quedará en la carpeta `dist/` como:
  - `dist/MonitorMemoria.exe`

### 3. Generar el ejecutable con icono personalizado

Asegúrate de tener el archivo de icono en formato `.ico`, por ejemplo:

- `Gemini_Generated_Image_w7k7jdw7k7jdw7k7.ico`

Luego ejecuta:

```bash
python -m PyInstaller --onefile --windowed --name MonitorMemoria --icon .\Gemini_Generated_Image_w7k7jdw7k7jdw7k7.ico demo.py
```

El ejecutable se generará en:

```text
C:\Users\gabri\Documents\GitHub\Memory_Sistems\dist\MonitorMemoria.exe
```

## Cómo usar el ejecutable en otras PCs

1. Copia el archivo `MonitorMemoria.exe` desde la carpeta `dist/` a la otra PC (USB, red, etc.).
2. No es necesario tener Python instalado en la otra máquina.
3. Ejecuta `MonitorMemoria.exe` con doble clic.

## Notas

- Algunas carpetas como `build/` y `dist/` pueden estar ignoradas en Git mediante `.gitignore`.
- Si modificas el código de `demo.py`, deberás volver a generar el ejecutable para que tome los cambios.
