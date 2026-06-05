#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo "  靶场实弹射击安全管控系统 - 前端启动"
echo "  端口: 9701"
echo "=========================================="

echo ""
echo "检查Node环境..."
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

echo ""
echo "Node版本: $(node --version)"
echo "NPM版本: $(npm --version)"

echo ""
echo "检查依赖..."
if [ ! -d "node_modules" ]; then
    echo ""
    echo "安装依赖包..."
    npm install
fi

echo ""
echo "=========================================="
echo "  启动Vue开发服务器 (端口 9701)"
echo "=========================================="
echo ""
echo "访问地址: http://localhost:9701"
echo ""

npm run dev
