from dirty_models import ArrayField, FloatField, IntegerField, ModelField, StringIdField, TimedeltaField

from . import BaseCollectionManager, BaseModelManager
from .message import BaseMessage
from ..models import BaseModel, DateTimeField
from ..results import Result


class Participant(BaseModel):
    """
    Live location participant model.
    """

    accuracy = IntegerField()
    """
    Location accuracy in meters.
    """

    comment = StringIdField()
    """
    Comment sent with live location message.
    """

    degrees = FloatField()
    """
    User direction in degrees.
    """

    expiration = DateTimeField()
    """
    When live location will expire.
    """

    last_update = DateTimeField()
    """
    Last update timestamp.
    """

    lat = FloatField()
    """
    Latitude.
    """

    lng = FloatField()
    """
    Longitude.
    """

    msg = ModelField(model_class=BaseMessage)
    """
    Message used to start live location.
    """

    sequence = IntegerField()
    """
    Sequence number.
    """

    speed = IntegerField()
    """
    User speed.
    """


class LiveLocation(BaseModel):
    """
    Live location model.
    """

    duration = TimedeltaField()
    """
    Live location duration.
    """

    participants = ArrayField(field_type=ModelField(model_class=Participant))
    """
    List of participants.
    """


class ParticipantManager(BaseModelManager[Participant]):
    """
    Participant manager.
    """

    MODEL_CLASS = Participant


class ParticipantCollectionManager(BaseCollectionManager[ParticipantManager]):
    """
    Participant collection manager. It allows manage live location participants.
    """

    MODEL_MANAGER_CLASS = ParticipantManager


class LiveLocationManager(BaseModelManager[LiveLocation]):
    """
    Live location manager.

    .. attribute:: participants

        :class:`~whalesong.managers.live_location.ParticipantCollectionManager`

        Live location's participants collection manager.
    """

    MODEL_CLASS = LiveLocation

    def __init__(self, driver, manager_path=''):
        super(LiveLocationManager, self).__init__(driver=driver, manager_path=manager_path)

        self.add_submanager('participants', ParticipantCollectionManager(
            driver=self._driver,
            manager_path=self._build_command('participants')
        ))

    def subscribe(self) -> Result[None]:
        """
        Subscribe to a live location. It is needed in order to receive updates.
        """
        return self._execute_command('subscribe')

    def unsubscribe(self) -> Result[None]:
        """
        Unsubscribe to a live location.
        """
        return self._execute_command('unsubscribe')

    def stop_my_live_location(self) -> Result[None]:
        """
        Stop to share current user live location in this chat.
        """
        return self._execute_command('stopMyLiveLocation')


class LiveLocationCollectionManager(BaseCollectionManager):
    """
    Live locations collection manager.
    """

    MODEL_MANAGER_CLASS = LiveLocationManager
