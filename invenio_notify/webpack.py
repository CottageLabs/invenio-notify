"""JS/CSS Webpack bundles for theme."""

from invenio_assets.webpack import WebpackThemeBundle

notify = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "invenio-administration-reviewer-search": "./js/invenio_notify/src/administration/reviewer/index.js",
            },
            dependencies={
                "@babel/runtime": "^7.9.0",
                "formik": "^2.2.9",
                "i18next": "^20.3.0",
                "i18next-browser-languagedetector": "^6.1.0",
                "luxon": "^1.23.0",
                "path": "^0.12.7",
                "prop-types": "^15.7.2",
                "react-copy-to-clipboard": "^5.0.0",
                "react-dnd": "^11.1.0",
                "react-dnd-html5-backend": "^11.1.0",
                "react-dropzone": "^11.0.0",
                "react-i18next": "^11.11.0",
                "react-invenio-forms": "^4.0.0",
                "react-searchkit": "^3.0.0",
                "tinymce": "^6.7.2",
                "@tinymce/tinymce-react": "^4.3.0",
                "yup": "^0.32.0",
            },
            aliases={
                # Define Semantic-UI theme configuration needed by
                # Invenio-Theme in order to build Semantic UI (in theme.js
                # entry point). theme.config itself is provided by
                # cookiecutter-invenio-rdm.
                "@js/invenio_notify": "js/invenio_notify",
                # "@translations/invenio_administration": "translations/invenio_administration",
            },
        ),
    },
)
