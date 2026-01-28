from django.urls import path
from .views import TickerListView, FinancialDataView, MarketSummaryView, LiveDataView

urlpatterns = [
    path('tickers/', TickerListView.as_view(), name='ticker-list'),
    path('data/<str:ticker>/', FinancialDataView.as_view(), name='financial-data'),
    path('live/<str:ticker>/', LiveDataView.as_view(), name='live-data'),
    path('summary/', MarketSummaryView.as_view(), name='market-summary'),
]
