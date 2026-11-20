# Before and after

Each pair shows one rule from [SKILL.md](SKILL.md) at work.

## Steps in order → numbered list

**Before:**

> To get started, you'll first want to make sure Node is installed, and once that's done you can clone the repository and then run npm install, after which you should copy the example env file to .env and finally start the dev server with npm run dev.

**After:**

> 5 steps:
>
> 1. Install Node 20 or later.
> 2. Clone the repo.
> 3. Run `npm install`.
> 4. Copy `.env.example` to `.env`.
> 5. Run `npm run dev`.

## Comparison → table

**Before:**

> Postgres is a relational database that's great for structured data and complex queries, and it supports transactions well. MongoDB, on the other hand, is a document store that's more flexible with schemas but historically had weaker transaction support, though that has improved. SQLite is file-based and really simple to set up, but it isn't designed for many concurrent writers.

**After:**

> **Use Postgres** unless you have a reason not to.
>
> | | Postgres | MongoDB | SQLite |
> |---|---|---|---|
> | **Data shape** | Tables | Documents | Tables |
> | **Setup** | Server | Server | One file |
> | **Many writers** | Yes | Yes | No |
> | **Best for** | Most apps | Changing schemas | Local and small apps |

## Debugging → Cause, Fix, Check

**Before:**

> It looks like the error you're seeing is probably happening because something else is already running on port 3000, which is pretty common if you had a previous dev server that didn't shut down properly. You could try finding and killing that process, or alternatively you could just change the port your app uses.

**After:**

> **Cause:** another process is using port 3000.
>
> **Fix:** stop it.
> ```
> lsof -ti :3000 | xargs kill
> ```
> **Check:** run `npm run dev` again. It starts without the error.

## Explanation → answer line, then bullets

**Before:**

> A closure is a concept in JavaScript and other languages where a function retains access to variables from the scope in which it was defined, even after that outer function has finished executing, which is useful for things like data privacy and creating function factories.

**After:**

> **A closure is a function that remembers the variables around it when it was created.**
>
> - **Keeps working:** it can read those variables after the outer function returns.
> - **Used for:** private state, and functions that build other functions.
