from base64 import b64encode
from dirty_models import StringIdField
from io import BytesIO

from . import BaseCollectionManager, BaseModelManager
from ..models import BaseModel
from ..results import Result


class ProfilePicture(BaseModel):
    eurl = StringIdField()
    """
    Url to contact picture.
    """

    raw = StringIdField()
    """
    ¿?
    """

    tag = StringIdField()
    """
    ¿?
    
    .. note:: I guess it is used to know when contact picture changed.
    """


class ProfilePictureManager(BaseModelManager[ProfilePicture]):
    """
    Profile picture manager. It allows manage a contact picture.
    """

    MODEL_CLASS = ProfilePicture

    def can_set(self) -> Result[bool]:
        """
        Whether can set a new picture or not.
        """

        return self._execute_command('canSet')

    def set_picture(self, picture: BytesIO, picture_preview: BytesIO = None) -> Result[bool]:
        """
        Set a new picture.
        """

        picture = b64encode(picture.read()).decode()

        if picture_preview:
            picture_preview = b64encode(picture_preview.read()).decode()

        return self._execute_command('setPicture', {'previewPicture': picture_preview,
                                                    'picture': picture})

    def can_delete(self) -> Result[bool]:
        """
        Whether can delete picture or not.
        """

        return self._execute_command('canDelete')

    def delete_picture(self) -> Result[bool]:
        """
        Delete current picture.
        """

        return self._execute_command('deletePicture')


class ProfilePictureCollectionManager(BaseCollectionManager[ProfilePictureManager]):
    """
    Profile picture collection manager.
    """

    MODEL_MANAGER_CLASS = ProfilePictureManager
