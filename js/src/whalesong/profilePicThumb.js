import {
  command
} from '../manager.js';
import {
  CollectionManager,
  ModelManager
} from './common.js';

export class ProfilePicThumbManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized
    });
  }

  @command
  async canSet() {
    return this.model.canSet();
  }

  @command
  async setPicture({
    picturePreview,
    picture
  }) {
    if (picturePreview) {
      picturePreview = 'data:image/jpeg;base64,' + picturePreview;
    }

    if (picture) {
      picture = 'data:image/jpeg;base64,' + picture;
    }
    return this.model.setPicture(picturePreview, picture);
  }

  @command
  async canDelete() {
    return this.model.canDelete();
  }

  @command
  async deletePicture() {
    return this.model.deletePicture();
  }
}

export class ProfilePicThumbCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return ProfilePicThumbManager;
  }
}