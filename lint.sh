# Script para executar linting e formatação
# Executa: bash lint.sh

echo "🔍 Executando verificações de código..."

echo "\n📏 Black - Formatação de código"
black app/ tests/ --check --diff

echo "\n🔎 Flake8 - Verificação de estilo"
flake8 app/ tests/

echo "\n✅ Verificações concluídas!"

echo "\n💡 Para aplicar correções automáticas do Black:"
echo "   black app/ tests/"
