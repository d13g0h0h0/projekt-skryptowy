# frontend

All the following commands should be run from the `/frontend` directory.
You should have `npm` installed on your machine in order to run them.

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

After you have started the Django backend, you can start the frontend:

```sh
npm run dev
```

You should now be able to see the website at `http://localhost:5173/`.

### Type-Check, Compile and Minify for Production

Before pushing your changes, you should run the following command:

```sh
npm run build
```

If the build fails, the current version must not be merged into the `main` branch.
