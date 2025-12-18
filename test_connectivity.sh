#!/bin/bash
# Script pour tester l'upload depuis le navigateur

echo "🔍 Test de connectivité Backend depuis l'hôte..."
echo ""

# Test 1: Backend accessible
echo "1️⃣ Test Backend Health..."
curl -s http://localhost:8000/health && echo " ✅" || echo " ❌"
echo ""

# Test 2: Backend API
echo "2️⃣ Test Dashboard Stats..."
curl -s http://localhost:8000/api/v1/dashboard/stats | jq '.total_evaluations' && echo " ✅" || echo " ❌"
echo ""

# Test 3: Upload
echo "3️⃣ Test Upload via curl..."
if [ -f "test_upload_unique_1766052089.csv" ]; then
    curl -X POST http://localhost:8000/api/v1/upload \
      -F "file=@test_upload_unique_1766052089.csv" \
      -s | jq '.message'
    echo " ✅"
else
    echo "⚠️  Fichier test_upload_unique_1766052089.csv introuvable"
fi
echo ""

# Test 4: CORS headers
echo "4️⃣ Vérification des headers CORS..."
curl -v http://localhost:8000/health 2>&1 | grep -i "access-control" || echo "⚠️  Pas de headers CORS visibles"
echo ""

echo "📊 Résumé:"
echo "  - Si tous les tests curl passent ✅"
echo "  - Mais le navigateur affiche 'Network Error'"
echo "  → Le problème est CORS ou configuration frontend"
echo ""
echo "📝 Action suivante:"
echo "1. Ouvrez http://localhost:3000 dans votre navigateur"
echo "2. Appuyez sur F12 (Console Développeur)"
echo "3. Allez dans l'onglet 'Network' / 'Réseau'"
echo "4. Essayez d'uploader un fichier"
echo "5. Regardez la requête '/upload' - quel est le status?"
