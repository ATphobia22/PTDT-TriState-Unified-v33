const { app, BrowserWindow } = require('electron');
const path = require('path');

app.commandLine.appendSwitch('enable-gpu-rasterization');
app.commandLine.appendSwitch('ignore-gpu-blocklist');
app.commandLine.appendSwitch('enable-zero-copy');
app.setAppUserModelId('com.ptdt.unified.v33');

function createWindow() {
  const win = new BrowserWindow({
    width: 1920,
    height: 1080,
    minWidth: 1280,
    minHeight: 720,
    backgroundColor: '#0a1628',
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
      backgroundThrottling: false,
    },
    title: 'PTDT Unified V33 — Virtual Tri-State River Valley',
  });

  win.once('ready-to-show', () => {
    win.show();
    win.focus();
  });

  win.loadFile(path.join(__dirname, '../dist/index.html'));
  win.setMenuBarVisibility(false);

  if (process.argv.includes('--dev')) {
    win.webContents.openDevTools({ mode: 'detach' });
  }
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
