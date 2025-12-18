"""
Service de clustering des évaluations
"""
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
import numpy as np
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClusteringService:
    """
    Service de clustering utilisant HDBSCAN, K-Means ou DBSCAN
    """
    
    def __init__(self):
        # Modèle d'embedding multilingue
        self.embedding_model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        logger.info("ClusteringService initialized with multilingual embeddings")
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Génère les embeddings pour une liste de textes
        
        Args:
            texts: Liste de textes
            
        Returns:
            Array numpy des embeddings
        """
        if not texts:
            return np.array([])
        
        try:
            embeddings = self.embedding_model.encode(
                texts,
                show_progress_bar=False,
                batch_size=settings.BATCH_SIZE
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return np.array([])
    
    # HDBSCAN removed - not available without C compilation
    # Using KMeans and DBSCAN as alternatives
    
    def cluster_kmeans(
        self,
        embeddings: np.ndarray,
        n_clusters: Optional[int] = None
    ) -> Tuple[np.ndarray, Dict[str, any]]:
        """
        Clustering avec K-Means
        
        Args:
            embeddings: Embeddings des textes
            n_clusters: Nombre de clusters (auto-déterminé si None)
            
        Returns:
            Tuple (cluster_labels, cluster_info)
        """
        if len(embeddings) == 0:
            return np.array([]), {}
        
        # Détermine le nombre de clusters selon les priorités :
        # 1. Paramètre explicite passé à la fonction
        # 2. Configuration DEFAULT_N_CLUSTERS (si défini)
        # 3. Auto-détection avec méthode du coude
        if n_clusters is None:
            if settings.DEFAULT_N_CLUSTERS is not None:
                n_clusters = settings.DEFAULT_N_CLUSTERS
                logger.info(f"Using configured DEFAULT_N_CLUSTERS: {n_clusters}")
            else:
                n_clusters = self._optimal_clusters_elbow(embeddings)
                logger.info(f"Auto-detected optimal clusters: {n_clusters}")
        
        try:
            # Normaliser les embeddings
            scaler = StandardScaler()
            scaled_embeddings = scaler.fit_transform(embeddings)
            
            # K-Means
            kmeans = KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10
            )
            cluster_labels = kmeans.fit_predict(scaled_embeddings)
            
            cluster_info = {
                "method": "kmeans",
                "n_clusters": n_clusters,
                "inertia": float(kmeans.inertia_),
                "cluster_sizes": {
                    int(label): int(np.sum(cluster_labels == label))
                    for label in range(n_clusters)
                },
                "centroids": kmeans.cluster_centers_.tolist()
            }
            
            return cluster_labels, cluster_info
            
        except Exception as e:
            logger.error(f"Error in K-Means clustering: {e}")
            return np.array([0] * len(embeddings)), {}
    
    def cluster_dbscan(
        self,
        embeddings: np.ndarray,
        eps: float = 0.5,
        min_samples: int = 5
    ) -> Tuple[np.ndarray, Dict[str, any]]:
        """
        Clustering avec DBSCAN
        
        Args:
            embeddings: Embeddings des textes
            eps: Distance maximale entre deux points
            min_samples: Nombre minimal de points pour un cluster
            
        Returns:
            Tuple (cluster_labels, cluster_info)
        """
        if len(embeddings) == 0:
            return np.array([]), {}
        
        try:
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            cluster_labels = dbscan.fit_predict(embeddings)
            
            unique_labels = set(cluster_labels)
            n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
            n_noise = list(cluster_labels).count(-1)
            
            cluster_info = {
                "method": "dbscan",
                "n_clusters": n_clusters,
                "n_noise": n_noise,
                "cluster_sizes": {
                    int(label): int(np.sum(cluster_labels == label))
                    for label in unique_labels if label != -1
                },
                "outliers": n_noise
            }
            
            return cluster_labels, cluster_info
            
        except Exception as e:
            logger.error(f"Error in DBSCAN clustering: {e}")
            return np.array([-1] * len(embeddings)), {}
    
    def cluster(
        self,
        texts: List[str],
        method: Optional[str] = None,
        **kwargs
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, any]]:
        """
        Pipeline complet de clustering
        
        Args:
            texts: Liste de textes à clustériser
            method: Méthode de clustering (kmeans, dbscan)
            **kwargs: Paramètres supplémentaires pour la méthode
            
        Returns:
            Tuple (embeddings, cluster_labels, cluster_info)
        """
        # Générer les embeddings
        embeddings = self.get_embeddings(texts)
        
        if len(embeddings) == 0:
            return np.array([]), np.array([]), {}
        
        # Sélectionner la méthode (default: kmeans)
        method = method or "kmeans"
        
        if method == "kmeans":
            cluster_labels, cluster_info = self.cluster_kmeans(embeddings, **kwargs)
        elif method == "dbscan":
            cluster_labels, cluster_info = self.cluster_dbscan(embeddings, **kwargs)
        else:
            logger.warning(f"Unknown clustering method: {method}, using K-Means")
            cluster_labels, cluster_info = self.cluster_kmeans(embeddings, **kwargs)
        
        return embeddings, cluster_labels, cluster_info
    
    def _optimal_clusters_elbow(self, embeddings: np.ndarray, max_k: Optional[int] = None) -> int:
        """
        Détermine le nombre optimal de clusters avec la méthode du coude
        
        Args:
            embeddings: Embeddings
            max_k: Nombre maximum de clusters à tester (uses settings.MAX_CLUSTERS if None)
            
        Returns:
            Nombre optimal de clusters
        """
        if len(embeddings) < 10:
            return min(3, len(embeddings))
        
        # Utiliser la configuration si max_k n'est pas spécifié
        if max_k is None:
            max_k = settings.MAX_CLUSTERS
        
        max_k = min(max_k, len(embeddings) // 2)
        
        inertias = []
        K_range = range(2, max_k + 1)
        
        scaler = StandardScaler()
        scaled_embeddings = scaler.fit_transform(embeddings)
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=5)
            kmeans.fit(scaled_embeddings)
            inertias.append(kmeans.inertia_)
        
        # Trouver le coude (approche simple)
        if len(inertias) >= 2:
            diffs = np.diff(inertias)
            optimal_k = np.argmax(diffs) + 2  # +2 car on commence à k=2
            return int(optimal_k)
        
        return 3  # Par défaut


# Instance globale
_clustering_service: Optional[ClusteringService] = None


def get_clustering_service() -> ClusteringService:
    """Retourne l'instance singleton de ClusteringService"""
    global _clustering_service
    if _clustering_service is None:
        _clustering_service = ClusteringService()
    return _clustering_service
