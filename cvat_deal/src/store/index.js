// store/index.js
import { createStore } from 'vuex';

const store = createStore({
  state: {
    sharedData: 'Hello from Vuex!',
    globalsetting_conf: {
      cookie: "",
      class_path: "",
      down_save_path: "",
      will_gen_save_path: "",
      gen_save_path: "",
      will_change_path: "",
      cvat_ip:"",
      serve_username: "",
      serve_password: ""
    },
  },
  mutations: {
    setGlobalSetting_conf(state, status) {
      state.globalsetting_conf = status;
    },
  },
});

export default store;