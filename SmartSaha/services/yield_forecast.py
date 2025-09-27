from SmartSaha.models import YieldRecord, YieldForecast
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

class YieldForecastService:
    def __init__(self, parcel_crop):
        self.parcel_crop = parcel_crop
        self.model = LinearRegression()

    def fetch_data(self):
        qs = YieldRecord.objects.filter(parcelCrop=self.parcel_crop).order_by("date")
        if not qs.exists():
            return None
        data = pd.DataFrame(list(qs.values("date", "yield_amount")))
        data["date_ordinal"] = pd.to_datetime(data["date"]).map(lambda d: d.toordinal())
        return data

    def train_model(self, data):
        X = data[["date_ordinal"]]
        y = data["yield_amount"]
        self.model.fit(X, y)

    def predict_next(self, days_ahead=7):
        data = self.fetch_data()
        if data is None or data.empty:
            return None

        self.train_model(data)

        last_date = data["date"].max()
        if isinstance(last_date, pd.Timestamp):
            next_date = (last_date + pd.Timedelta(days=days_ahead)).date()
        else:
            next_date = last_date + pd.Timedelta(days=days_ahead)

        X_pred = pd.DataFrame([[next_date.toordinal()]], columns=["date_ordinal"])
        predicted_yield = self.model.predict(X_pred)[0]
        return next_date, predicted_yield

    def save_forecast(self, days_ahead=7):
        result = self.predict_next(days_ahead)
        if result is None:
            return None
        forecast_date, predicted_yield = result

        # Vérifier si une prévision existe déjà
        existing = YieldForecast.objects.filter(
            parcelCrop=self.parcel_crop,
            forecast_date=forecast_date
        ).first()

        if existing:
            # Retourner l’existant au lieu de recréer
            return existing

        forecast = YieldForecast.objects.create(
            parcelCrop=self.parcel_crop,
            forecast_date=forecast_date,
            predicted_yield=predicted_yield
        )
        return forecast



class YieldAnalyticsService:
    def __init__(self, user=None):
        self.user = user

    def load_data(self):
        qs = YieldRecord.objects.select_related("parcelCrop__parcel")
        if self.user:
            qs = qs.filter(parcelCrop__parcel__owner=self.user)

        df = pd.DataFrame(list(qs.values("date", "yield_amount", "area", "parcelCrop_id")))
        if df.empty:
            return None
        df["year"] = pd.to_datetime(df["date"]).dt.year
        df["yield_per_area"] = df["yield_amount"] / df["area"]
        return df

    def generate_histogram(self, df, path="histogram_yield.png"):
        plt.figure()
        df["yield_amount"].plot.hist(bins=20, alpha=0.7)
        plt.title("Distribution des rendements")
        plt.xlabel("Rendement")
        plt.ylabel("Fréquence")
        plt.savefig(path)
        return path

    def generate_boxplot(self, df, path="boxplot_yield_by_year.png"):
        plt.figure()
        df.boxplot(column="yield_amount", by="year")
        plt.title("Variation annuelle des rendements")
        plt.suptitle("")
        plt.xlabel("Année")
        plt.ylabel("Rendement")
        plt.savefig(path)
        return path

    def generate_trend(self, df, path="trend_yield_by_year.png"):
        plt.figure()
        df.groupby("year")["yield_amount"].mean().plot(marker="o")
        plt.title("Tendance des rendements moyens par an")
        plt.xlabel("Année")
        plt.ylabel("Rendement moyen")
        plt.grid(True)
        plt.savefig(path)
        return path

    def generate_yield_per_area(self, df, path="yield_per_area_by_parcel.png"):
        plt.figure()
        for parcel_id, group in df.groupby("parcelCrop_id"):
            group.groupby("year")["yield_per_area"].mean().plot(marker="x", label=f"Parcelle {parcel_id}")
        plt.title("Rendement par surface (t/ha) par parcelle")
        plt.xlabel("Année")
        plt.ylabel("Rendement/ha")
        plt.legend()
        plt.grid(True)
        plt.savefig(path)
        return path

    def run_all(self, save_dir="."):
        df = self.load_data()
        if df is None:
            return []

        files = []
        files.append(self.generate_histogram(df, f"{save_dir}/histogram_yield.png"))
        files.append(self.generate_boxplot(df, f"{save_dir}/boxplot_yield_by_year.png"))
        files.append(self.generate_trend(df, f"{save_dir}/trend_yield_by_year.png"))
        files.append(self.generate_yield_per_area(df, f"{save_dir}/yield_per_area_by_parcel.png"))

        return files


    def get_user_stats(self):
        records = YieldRecord.objects.select_related("parcelCrop__parcel") \
            .filter(parcelCrop__parcel__owner=self.user)

        if not records.exists():
            return {}

        data = list(records.values(
            "parcelCrop_id",
            "parcelCrop__parcel__parcel_name",
            "date",          # <-- utilise date
            "yield_amount",
            "area"
        ))
        df = pd.DataFrame(data)

        # Ajouter la colonne 'year' depuis la date
        df["year"] = pd.to_datetime(df["date"]).dt.year

        # Rendement par hectare
        df["yield_per_area"] = df["yield_amount"] / df["area"]

        stats_json = {}
        for parcel_id, group in df.groupby("parcelCrop_id"):
            stats_json[parcel_id] = {
                "parcel_name": group["parcelCrop__parcel__parcel_name"].iloc[0],
                "years": group["year"].tolist(),
                "dates": group["date"].astype(str).tolist(),
                "yield_amount": group["yield_amount"].tolist(),
                "yield_per_area": group["yield_per_area"].tolist(),
                "mean_yield": group["yield_amount"].mean(),
                "mean_yield_per_area": group["yield_per_area"].mean(),
            }
        return stats_json

