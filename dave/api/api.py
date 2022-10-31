# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import uvicorn
from fastapi import FastAPI

from dave.api.routes import router
from dave.toolbox import auth_available

# Wait until DAVE authentication server is ready
auth_available()

# initialize app object
app = FastAPI()

# include routes
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=9000, reload=True)
