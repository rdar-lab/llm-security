import { createStore } from 'vuex'
import auth from './modules/auth'
import transactions from './modules/transactions'
import protections from './modules/protections'

const store = createStore({
    modules: {
        auth,
        transactions,
        protections
    }
})

export default store