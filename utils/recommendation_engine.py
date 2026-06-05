"""
SmartRecommend - Machine Learning Engine
Hybrid recommendation system: Content-Based + Collaborative Filtering
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import pickle
import os
import warnings
warnings.filterwarnings("ignore")


class ContentBasedRecommender:
    """TF-IDF + Cosine Similarity on product descriptions, tags, categories"""
    
    def __init__(self):
        self.tfidf = TfidfVectorizer(
            max_features=1000,
            stop_words="english",
            ngram_range=(1, 2)
        )
        self.similarity_matrix = None
        self.products_df = None

    def fit(self, products_df: pd.DataFrame):
        self.products_df = products_df.reset_index(drop=True)
        # Combine features for richer similarity
        features = (
            products_df["description"].fillna("") + " " +
            products_df["category"].fillna("") + " " +
            products_df["tags"].fillna("") + " " +
            products_df["brand"].fillna("") + " " +
            products_df["name"].fillna("")
        )
        tfidf_matrix = self.tfidf.fit_transform(features)
        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        return self

    def recommend(self, product_id: int, n: int = 10) -> pd.DataFrame:
        if self.products_df is None:
            return pd.DataFrame()
        
        idx_series = self.products_df[self.products_df["product_id"] == product_id].index
        if len(idx_series) == 0:
            return pd.DataFrame()
        
        idx = idx_series[0]
        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = [(i, s) for i, s in sim_scores if i != idx][:n * 2]
        
        product_indices = [i[0] for i in sim_scores]
        scores = [i[1] for i in sim_scores]
        
        result = self.products_df.iloc[product_indices].copy()
        result["content_score"] = scores
        return result.head(n)

    def get_category_recommendations(self, category: str, n: int = 10) -> pd.DataFrame:
        if self.products_df is None:
            return pd.DataFrame()
        cat_products = self.products_df[self.products_df["category"] == category]
        if cat_products.empty:
            return pd.DataFrame()
        # Return top-rated in category
        return cat_products.nlargest(n, "rating")


class CollaborativeFilteringRecommender:
    """User-based collaborative filtering using NearestNeighbors"""
    
    def __init__(self):
        self.model = NearestNeighbors(n_neighbors=20, metric="cosine", algorithm="brute")
        self.user_product_matrix = None
        self.products_df = None
        self.fitted = False

    def fit(self, ratings_df: pd.DataFrame, products_df: pd.DataFrame):
        self.products_df = products_df
        
        if ratings_df.empty or len(ratings_df) < 10:
            return self
        
        # Build user-product matrix
        matrix = ratings_df.pivot_table(
            index="user_id",
            columns="product_id",
            values="rating",
            aggfunc="mean"
        ).fillna(0)
        
        self.user_product_matrix = matrix
        
        if matrix.shape[0] > 5:
            self.model.fit(matrix.values)
            self.fitted = True
        return self

    def recommend_for_user(self, user_id: int, n: int = 10) -> pd.DataFrame:
        if not self.fitted or self.user_product_matrix is None:
            return pd.DataFrame()
        
        if user_id not in self.user_product_matrix.index:
            # New user - return popular products
            return self.products_df.nlargest(n, "purchases")
        
        user_idx = self.user_product_matrix.index.get_loc(user_id)
        user_vec = self.user_product_matrix.values[user_idx].reshape(1, -1)
        
        distances, indices = self.model.kneighbors(user_vec, n_neighbors=min(10, self.user_product_matrix.shape[0]))
        similar_users_indices = indices[0][1:]  # exclude self
        
        # Products liked by similar users
        similar_users_ids = self.user_product_matrix.index[similar_users_indices]
        similar_ratings = self.user_product_matrix.loc[similar_users_ids]
        
        # Already rated/seen products by this user
        user_rated = set(self.user_product_matrix.columns[self.user_product_matrix.loc[user_id] > 0])
        
        # Score products by similar user ratings
        product_scores = similar_ratings.mean(axis=0)
        product_scores = product_scores[~product_scores.index.isin(user_rated)]
        product_scores = product_scores.nlargest(n)
        
        if product_scores.empty:
            return self.products_df.nlargest(n, "purchases")
        
        recommended_ids = product_scores.index.tolist()
        result = self.products_df[self.products_df["product_id"].isin(recommended_ids)].copy()
        result["collab_score"] = result["product_id"].map(product_scores.to_dict())
        return result.head(n)

    def get_similar_items(self, product_id: int, n: int = 5) -> pd.DataFrame:
        """Items frequently bought/rated together"""
        if self.user_product_matrix is None:
            return pd.DataFrame()
        
        if product_id not in self.user_product_matrix.columns:
            return pd.DataFrame()
        
        product_col = self.user_product_matrix[product_id]
        correlations = {}
        
        for col in self.user_product_matrix.columns:
            if col != product_id:
                try:
                    corr = product_col.corr(self.user_product_matrix[col])
                    if not np.isnan(corr):
                        correlations[col] = corr
                except:
                    pass
        
        if not correlations:
            return pd.DataFrame()
        
        top_ids = sorted(correlations, key=correlations.get, reverse=True)[:n]
        result = self.products_df[self.products_df["product_id"].isin(top_ids)].copy()
        result["item_collab_score"] = result["product_id"].map(correlations)
        return result


class HybridRecommender:
    """
    Hybrid Recommendation Engine
    Score = 0.6 × Content Similarity + 0.4 × Collaborative Score
    """
    
    CONTENT_WEIGHT = 0.6
    COLLAB_WEIGHT = 0.4
    
    def __init__(self):
        self.content_rec = ContentBasedRecommender()
        self.collab_rec = CollaborativeFilteringRecommender()
        self.products_df = None
        self.scaler = MinMaxScaler()

    def fit(self, products_df: pd.DataFrame, ratings_df: pd.DataFrame):
        self.products_df = products_df
        print("  Fitting content-based recommender...")
        self.content_rec.fit(products_df)
        print("  Fitting collaborative filter...")
        self.collab_rec.fit(ratings_df, products_df)
        print("  Hybrid engine ready!")
        return self

    def recommend_similar(self, product_id: int, n: int = 6) -> pd.DataFrame:
        """Recommend products similar to a given product"""
        content_recs = self.content_rec.recommend(product_id, n=n * 2)
        
        if content_recs.empty:
            return self.products_df.sample(min(n, len(self.products_df)))
        
        # Normalize content scores
        if len(content_recs) > 1:
            content_recs["content_score_norm"] = self.scaler.fit_transform(
                content_recs[["content_score"]]
            ).flatten()
        else:
            content_recs["content_score_norm"] = 1.0
        
        # Get collaborative scores for these products
        collab_scores = {}
        if self.collab_rec.user_product_matrix is not None:
            for pid in content_recs["product_id"]:
                if pid in self.collab_rec.user_product_matrix.columns:
                    avg_rating = self.collab_rec.user_product_matrix[pid].mean()
                    collab_scores[pid] = avg_rating / 5.0
        
        content_recs["collab_score_norm"] = content_recs["product_id"].map(
            lambda x: collab_scores.get(x, 0.5)
        )
        
        # Hybrid score
        content_recs["hybrid_score"] = (
            self.CONTENT_WEIGHT * content_recs["content_score_norm"] +
            self.COLLAB_WEIGHT * content_recs["collab_score_norm"]
        )
        
        return content_recs.nlargest(n, "hybrid_score")

    def recommend_for_user(self, user_id: int, viewed_products: list = None, n: int = 10) -> pd.DataFrame:
        """Personalized recommendations for a user"""
        # Collaborative picks
        collab_recs = self.collab_rec.recommend_for_user(user_id, n=n * 2)
        
        # Content picks from recently viewed
        content_recs_list = []
        if viewed_products:
            for pid in viewed_products[-3:]:  # last 3 viewed
                c_recs = self.content_rec.recommend(pid, n=5)
                if not c_recs.empty:
                    content_recs_list.append(c_recs)
        
        if content_recs_list:
            content_recs = pd.concat(content_recs_list).drop_duplicates("product_id")
        else:
            content_recs = self.products_df.nlargest(n, "rating")
        
        # Merge and score
        if collab_recs.empty:
            return content_recs.head(n)
        
        all_pids = set(collab_recs["product_id"].tolist() + content_recs["product_id"].tolist())
        candidates = self.products_df[self.products_df["product_id"].isin(all_pids)].copy()
        
        collab_score_map = dict(zip(collab_recs["product_id"], 
                                     collab_recs.get("collab_score", pd.Series(dtype=float)).values if "collab_score" in collab_recs.columns else [0.5]*len(collab_recs)))
        content_score_map = dict(zip(content_recs["product_id"], 
                                      content_recs.get("content_score", pd.Series(dtype=float)).values if "content_score" in content_recs.columns else [0.5]*len(content_recs)))
        
        candidates["collab_score_norm"] = candidates["product_id"].map(lambda x: collab_score_map.get(x, 0) / 5.0 if collab_score_map.get(x, 0) > 1 else collab_score_map.get(x, 0))
        candidates["content_score_norm"] = candidates["product_id"].map(lambda x: min(content_score_map.get(x, 0), 1.0))
        candidates["hybrid_score"] = (
            self.COLLAB_WEIGHT * candidates["collab_score_norm"] +
            self.CONTENT_WEIGHT * candidates["content_score_norm"]
        )
        
        return candidates.nlargest(n, "hybrid_score")

    def get_trending(self, n: int = 10) -> pd.DataFrame:
        """Trending products by views + purchases + rating"""
        if self.products_df is None:
            return pd.DataFrame()
        
        df = self.products_df.copy()
        scaler = MinMaxScaler()
        
        for col in ["views", "purchases", "rating"]:
            if col in df.columns:
                df[f"{col}_norm"] = scaler.fit_transform(df[[col]]).flatten()
        
        df["trend_score"] = (
            0.4 * df.get("views_norm", 0) +
            0.4 * df.get("purchases_norm", 0) +
            0.2 * df.get("rating_norm", 0)
        )
        return df.nlargest(n, "trend_score")

    def get_new_arrivals(self, n: int = 10) -> pd.DataFrame:
        """Simulate new arrivals - highest product_id (recently added)"""
        if self.products_df is None:
            return pd.DataFrame()
        return self.products_df.nlargest(n, "product_id")

    def explain_recommendation(self, product_id: int, user_id: int = None,
                                 viewed_products: list = None, liked_categories: list = None) -> dict:
        """Generate human-readable explanation for a recommendation"""
        reasons = []
        tags = []
        confidence = 75
        
        if self.products_df is None:
            return {"reasons": reasons, "tags": tags, "confidence": confidence}
        
        product = self.products_df[self.products_df["product_id"] == product_id]
        if product.empty:
            return {"reasons": reasons, "tags": tags, "confidence": confidence}
        
        p = product.iloc[0]
        
        if viewed_products and product_id in viewed_products:
            reasons.append("Based on your recent views")
            confidence += 5
        
        if liked_categories and p["category"] in liked_categories:
            reasons.append(f"Matches your interest in {p['category']}")
            tags.append("Your preferred category")
            confidence += 8
        
        if p["rating"] >= 4.5:
            reasons.append(f"Highly rated ({p['rating']}/5.0) by users")
            tags.append("Top rated")
            confidence += 5
        
        if p.get("purchases", 0) > 200:
            reasons.append("Popular among users with similar interests")
            tags.append("High popularity")
            confidence += 5
        
        if user_id:
            reasons.append("Users with similar preferences purchased this")
            tags.append("Recommended by AI")
            confidence += 7
        
        if not reasons:
            reasons = ["Trending in your area", "Matches your browsing pattern"]
            tags = ["Trending now"]
        
        confidence = min(confidence, 97)
        return {"reasons": reasons, "tags": tags, "confidence": confidence}

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path: str) -> "HybridRecommender":
        with open(path, "rb") as f:
            return pickle.load(f)


def build_and_save_model(products_csv: str, ratings_csv: str, model_path: str):
    """Build the full ML pipeline and save the model"""
    print("Loading data...")
    products_df = pd.read_csv(products_csv)
    ratings_df = pd.read_csv(ratings_csv)
    
    print(f"Products: {len(products_df)}, Ratings: {len(ratings_df)}")
    print("Building hybrid recommendation model...")
    
    engine = HybridRecommender()
    engine.fit(products_df, ratings_df)
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    engine.save(model_path)
    print(f"Model saved to {model_path}")
    return engine


if __name__ == "__main__":
    build_and_save_model(
        "data/products.csv",
        "data/ratings.csv",
        "models/recommendation_model.pkl"
    )
    print("✅ Model built and saved!")
