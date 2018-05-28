import {run} from '@cycle/run';
import {Stream} from 'xstream';
import {div, button, h1, h4, a, makeDOMDriver, DOMSource} from '@cycle/dom';
import {makeHTTPDriver, Response, HTTPSource} from '@cycle/http';

    function main(sources) {
        var getRandomUser$ = sources.DOM.select('.get-random').events('click')
            .map(function () {
            var randomNum = Math.round(Math.random() * 9) + 1;
            return {
                url: 'http://localhost:5000/profile/' + String(randomNum),
                category: 'users',
                method: 'GET',
            };
        });
        var user$ = sources.HTTP.select('users')
            .flatten()
            .map(function (res) { return res.body; })
            .startWith(null);
        var vdom$ = user$.map(function (user) {
            return div('.users', [
                button('.get-random', 'Get random user'),
                user === null ? null : div('.user-details', [
                    h1('.user-name', user.name),
                    h4('.user-email', user.email),
                    a('.user-website', { attrs: { href: user.website } }, user.website),
                ]),
            ]);
        });
        return {
            DOM: vdom$,
            HTTP: getRandomUser$,
        };
    }
    run(main, {
        DOM: makeDOMDriver('#randomuser'),
        HTTP: makeHTTPDriver(),
    });
