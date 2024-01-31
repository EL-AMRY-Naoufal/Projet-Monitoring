from controller import app

import os
if __name__ == '__main__':
    port:int=int(os.environ.get('PORT',5050))
    app.run(debug=True,host='0.0.0.0',port=5050)