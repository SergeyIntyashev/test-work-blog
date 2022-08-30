import logging
import traceback

from django.http import JsonResponse
from rest_framework.generics import GenericAPIView

# Параметры для отображения кирилических символов в JSON
JSON_DUMPS_PARAMS = {
    'ensure_ascii': False
}

logger = logging.getLogger(__name__)


class BaseView(GenericAPIView):
    """
    Базовый класс для всех view, обрабатывает исключения
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(traceback.format_exc())
            return self._response({f'errorMessage: {e}'}, status=400)

        if isinstance(response, (dict, list)):
            return self._response(response)
        else:
            return response

    @staticmethod
    def _response(data, *, status=200):
        """
        Возвращает response с данными в формате JSON
        """
        return JsonResponse(
            data,
            status=status,
            safe=not isinstance(data, list),
            json_dumps_params=JSON_DUMPS_PARAMS
        )
