Vue.component('navbar', {
    template:`
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <a class="navbar-brand text-success" href="#">T O A D</a>
        <button
        class="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
        >
        <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                <li class="nav-item" v-bind:class="{active:home}">
                    <a class="nav-link" href="#">Home<span class="sr-only">(current)</span></a>
                </li>
                <li class="nav-item" v-bind:class="{active:group_creation}">
                    <a class="nav-link" href="#">Group creation</a>
                </li>
                <li class="nav-item" v-bind:class="{active:shares}">
                    <a class="nav-link" href="#">Available Shares</a>
                </li>
            </ul>
            <ul class="navbar-nav navbar-right">
                <li class="nav-item" v-bind:class="{active:register}">
                    <a class="nav-link" href="/auth/register"><i class="fas fa-user-plus"></i> Sign Up</a>
                </li>
                <li class="nav-item" v-bind:class="{active:login}">
                    <a class="nav-link" href="/auth/login"><i class="fas fa-sign-in-alt"></i> Sign in</a>
                </li>
            </ul>
        </div>
    </nav>
    `,
    props:['tab'],
    computed: {
        group_creation: function() {
            return (this.tab=="group_creation") ? true:false;
        },
        shares: function() {
            return (this.tab=="shares") ? true:false;
        },
        home: function() {
            return (this.tab=="home") ? true:false;
        },
        login: function() {
            return (this.tab=="login") ? true:false;
        },
        register: function() {
            return (this.tab=="register") ? true:false;
        }

    },

})

Vue.component('banner',{
    template:`
    <div class="jumbotron bg-success mb-0" style="border-radius:0; height:200px">
    <img :src="url" height=100 class="float-left">
    <h2 class="text-white float-left">ThreshOld Anonymous Decryption protocol</h2>
    </div>
    `,
    data (){
        return {
            url : "/static/logo.png",
        }
    }
})

const vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
})

