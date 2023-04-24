from flask import Flask
from Embedding_Inference.append_coordinate_update.coordinate import coordinate


app = Flask(__name__)

@app.route('/')
def root():
    # update database
    crud, x_coord, y_coord, z_coord, reqIds, keywords1, keywords2, keywords3, keywords4 = coordinate()
    try:
        for p1, p2, p3, i, k1, k2, k3, k4 in zip(x_coord, y_coord, z_coord, reqIds, keywords1, keywords2, keywords3, keywords4):
            crud.updateDB_skyIslandCoord('skyisland', 'tbl_sky_island_coordinate', int(i), k1, k2, k3, k4, p1, p2, p3)
    except:
        pass

    return 'APPEND UPDATE COMPLETE !'

if __name__ == '__main__':
    app.run()