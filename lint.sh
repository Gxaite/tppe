# Script para executar linting e formatação
# Executa: bash lint.sh

echo "🔍 Executando verificações de código..."

echo "\n📏 Black - Formatação de código"
black backend/app/ backend/tests/ --check --diff

echo "\n🔎 Flake8 - Verificação de estilo"
flake8 backend/app/ backend/tests/

echo "\n✅ Verificações concluídas!"

echo "\n💡 Para aplicar correções automáticas do Black:"
echo "   black backend/app/ backend/tests/"
