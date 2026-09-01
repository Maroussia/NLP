# Miniforge + JupyterLab on Mac (true beginner guide)

This guide helps you run Jupyter notebooks on a Mac **without** Anaconda Navigator (which often fails on older macOS).

You will:
1) Download **Miniforge** (a lightweight installer)
2) Install it using your **Terminal**
3) Create a **course environment**
4) Launch **JupyterLab**

---

## Before you start

### A) Find out if your Mac is Intel or Apple Silicon
1. Click the **Apple menu ()** → **About This Mac**
2. Look for:
   - **Chip** = Apple M1 / M2 / M3 → **Apple Silicon**
   - **Processor** = Intel … → **Intel**

### B) Open Terminal
1. Press **Command (⌘) + Space** to open Spotlight search
2. Type **Terminal**
3. Press **Enter**

Terminal is a text-based way to run commands to your computer. You can copy/paste the commands from this guide.

---

## Step 1 — Download the Miniforge installer

1. Open your browser.
2. Open the page for **Miniforge** releases: https://github.com/conda-forge/miniforge/releases.
3. Download the installer that matches your Mac:

- **Apple Silicon (M1/M2/M3):** a file ending in
  - `Miniforge3-MacOSX-arm64.sh`
- **Intel Mac:** a file ending in
  - `Miniforge3-MacOSX-x86_64.sh`

Make sure the downloaded file ends with **`.sh`** and is in your **Downloads** folder.

---

## Step 2 — Go to your Downloads folder in Terminal

In Terminal, copy/paste this line and press **Enter**:

```bash
cd ~/Downloads
```

Now list the files in Downloads:

```bash
ls
```

You should see a Miniforge file like:
- `Miniforge3-MacOSX-arm64.sh` (Apple Silicon)
- `Miniforge3-MacOSX-x86_64.sh` (Intel)

If you do NOT see it, the download may be in a different folder (or not finished downloading).

---

## Step 3 — Run the installer

### A) Run the installer command
Type **bash**, then a space, then the installer filename.

For **Apple Silicon** (example):
```bash
bash Miniforge3-MacOSX-arm64.sh
```

For **Intel** (example):
```bash
bash Miniforge3-MacOSX-x86_64.sh
```

Tip: you can type `bash Mini` and then press **Tab** to auto-complete the filename.

### B) Follow the prompts (important)
During installation you will see prompts like these:

1. **License**: press **Space** to scroll; when it ends you can proceed.
2. When asked **“Do you accept the license terms?”** type:
   ```
   yes
   ```
   then press **Enter**.
3. When asked **install location**, press **Enter** to accept the default (recommended).
4. When asked **“Do you wish the installer to initialize Miniforge3 by running conda init?”** type:
   ```
   yes
   ```
   then press **Enter**.

### C) Close and reopen Terminal
When the installer finishes:
1. **Quit Terminal** (Terminal → Quit Terminal)
2. Open **Terminal** again

This makes sure the new settings are loaded.

---

## Step 4 — Check that `conda` works

In the new Terminal window, run:

```bash
conda --version
```

You should see something like `conda 24.x.x` (version number may differ).

If you see **“conda: command not found”**, go to **Troubleshooting** at the end.

---

## Step 5 — Create your course environment (from the YAML file)

Your course includes a file called:

- `environment-conda.yml`

and it is inside a folder called:

- `NLP`

### A) Go to the NLP folder
Make sure you downloaded the NLP folder and saved it in `Downloads`.

```bash
cd ~/Downloads/NLP
```

If Terminal says “No such file or directory”, your `NLP` folder may be somewhere else. Find it and move it to your `Downloads` folder. Then type again:

```bash
cd ~/Downloads/NLP
```

### B) Check that the file is there
Run:

```bash
ls
```

You should see `environment-conda.yml` in the list.

### C) Create the environment from the file
Run:

```bash
conda env create -f environment-conda.yml
```

This will take a few minutes.

### D) Activate the environment
Activate the environment by typing the following command in your terminal:

```bash
conda activate nlp
```

Your Terminal prompt should change to show something like:

```
(nlp) ...
```

---

## Step 6 — Start JupyterLab

With `(nlp)` active, type in your terminal:

```bash
jupyter lab
```

What should happen:
- A browser window opens to JupyterLab, or
- Terminal prints a URL like `http://localhost:8888/...` — copy/paste it into your browser.

### To stop JupyterLab
1. Click back into the Terminal window running Jupyter
2. Press **Control + C**
3. If asked “Shutdown this server (y/[n])?” type `y` and press Enter.

---

## How to start Jupyter lab when you have shut it down

1) Open your **Terminal**
2) Activate the environment by typing:
```bash
conda activate nlp
```
3) Start JupyterLab by typing:
```bash
jupyter lab
```

---

## Troubleshooting (common issues)

### 1) “conda: command not found”
Try these in order:

**A) Close and reopen Terminal**, then try:
```bash
conda --version
```

**B) Try to activate Miniforge directly (temporary fix):**
```bash
source ~/miniforge3/bin/activate
conda --version
```

**C) Initialize conda for zsh (most Macs use zsh):**
```bash
~/miniforge3/bin/conda init zsh
```
Then **close and reopen Terminal**.

If your Mac uses bash instead, run:
```bash
~/miniforge3/bin/conda init bash
```

---

### 2) Installer says “Permission denied”
Make the file executable, then run it again:

```bash
cd ~/Downloads
chmod +x Miniforge3-MacOSX-*.sh
bash Miniforge3-MacOSX-*.sh
```

---

### 3) Jupyter opens but kernel won’t run / Python version errors
This usually means the wrong environment is active.

1) Stop JupyterLab (Control+C)
2) Activate the environment:
```bash
conda activate course
```
3) Start again:
```bash
jupyter lab
```

Inside JupyterLab, select the correct kernel:
- **Kernel → Change Kernel → Python (course)** (wording may vary)

---

### 4) “PackagesNotFoundError” or solve errors on very old macOS
Try a slightly older Python:

```bash
conda create -n course python=3.9 jupyterlab ipykernel -y
conda activate course
jupyter lab
```

If even that fails, the macOS version may be too old for modern packages.

---

