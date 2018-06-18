import MainManager from './manager.js';
import createManagers from './whalesong/index.js'


window.manager = new MainManager();

createManagers(window.manager);