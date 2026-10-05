from app.app_model import AppModel
from app.feature.analysis.analyze_view_speed import AnalyzeSpeedView


class AnalyzeSpeedController:
    """Keep the propagation view synchronized with the filtered recording."""

    def __init__(self, app_model: AppModel, view: AnalyzeSpeedView):
        self.app_model = app_model
        self.view = view
        app_model.experiment_data_changed.connect(self.update_ui_from_model)
        self.update_ui_from_model()

    def update_ui_from_model(self) -> None:
        """Pass the recording and its saved boundaries to the view."""
        self.view.set_data(
            self.app_model.filtered_data_df,
            self.app_model.experiment_metadata,
            self.app_model.experiment_config,
        )
