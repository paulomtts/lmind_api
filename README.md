# cookbook_api 🍔
This is the API for the Cookbook app! The goal is to be a simple demonstration of FastAPI, SQLAlchemy, SQLModel & Pandas usage in building easy to read interactions with a database. Here are a few features:

- Nested, bulk & returning operations
- Object oriented chained operations
- Pandas lets you manipulate data with ease
- Complex queries (see queries.py and its use in routes.py's /custom/submit_recipe)
- Writing & syntax is a piece of 🍰
- You don't need to worry about parsing to JSON while writing custom routes

To achieve this, simply write a route like the one below:
```
@customRoutes_router.get("/my_route/")
async def my_route(input: YourSchema) -> APIOutput:

    @api_output
    @db.catching(messages=SuccessMessages('Submission succesful.'))
    def submit_data(form_data, upsert_data):
        form_object = db.upsert(Recipes, [form_data], single=True)
        upserted_df = db.upsert(RecipeIngredients, [{**row, 'id_recipe': form_object.id} for row in upsert_data])

        return = {
            'form_data': form_object
            , 'upserted_rows': upserted_df
        }

    return submit_data(form_data, upsert_data)
```

This project is usable out of the box, but don't forget to setup your enviroment variables! 🚀

All the thanks to @tiangolo. FastAPI is a really amazing piece of software!

## Comming up
- Private recipes
- Image files upload route
