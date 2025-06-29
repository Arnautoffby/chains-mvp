{ pkgs }:
{
  deps = [
    pkgs.python311Full      # интерпретатор Python 3.11
    pkgs.python311Packages.pip
    pkgs.postgresql         # клиент libpq для asyncpg
    pkgs.openssl            # TLS для aiohttp
    pkgs.libffi             # зависимость cffi, используется pydantic-core
  ];

  # Переменные окружения, отключающие user-site и обновления pip
  env = {
    PIP_DISABLE_PIP_VERSION_CHECK = "1";
    PYTHONNOUSERSITE = "";
  };
} 