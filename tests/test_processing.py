import pandas as pd
from src.backend.processing import filter_target_year

def test_filter_target_year_keeps_only_target():
    # Arrange : créer un mini DataFrame avec plusieurs années
    df = pd.DataFrame(
        {
            "session": [2024, 2025, 2026],
            "valeur": ["a", "b", "c"],
        }
    )

    # Act : appliquer le filtre sur 2026
    df_filtered = filter_target_year(df, 2026)

    # Assert : vérifier que seule l'année 2026 reste
    assert set(df_filtered["session"]) == {2026}
    assert len(df_filtered) == 1
