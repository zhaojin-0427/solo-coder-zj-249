#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo "  靶场实弹射击安全管控系统 - 后端启动"
echo "  端口: 9702"
echo "=========================================="

echo ""
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请先安装Python 3"
    exit 1
fi

echo ""
echo "检查虚拟环境..."
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo ""
echo "激活虚拟环境..."
source venv/bin/activate

echo ""
echo "安装依赖..."
pip install -r requirements.txt

echo ""
echo "执行数据库迁移..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "检查数据库是否已初始化..."
DB_COUNT=$(python -c "import django; django.setup(); from range_app.models import Shooter; print(Shooter.objects.count())" 2>/dev/null || echo "0")

if [ "$DB_COUNT" -eq "0" ]; then
    echo ""
    echo "初始化基础数据和测试数据..."
    python init_data.py
fi

echo ""
echo "创建超级用户(如果不存在)..."
python -c "
import django
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print('超级用户创建成功: admin / admin123456')
else:
    print('超级用户已存在: admin / admin123456')
"

echo ""
echo "=========================================="
echo "  启动Django服务器 (端口 9702)"
echo "=========================================="
echo ""
echo "API地址: http://localhost:9702/api/"
echo "管理后台: http://localhost:9702/admin/"
echo "用户名: admin  密码: admin123456"
echo ""

python manage.py runserver 0.0.0.0:9702
