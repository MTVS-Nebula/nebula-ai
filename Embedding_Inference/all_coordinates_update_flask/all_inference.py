from flask import Flask
from Embedding_Inference.all_coordinates_update_flask import coordinate


app = Flask(__name__)

@app.route('/')
def root():
    crud, x_coord, y_coord, z_coord, reqIds, keywords1, keywords2 = coordinate()
    for p1, p2, p3, i, k1, k2 in zip(x_coord, y_coord, z_coord, reqIds, keywords1, keywords2):
        crud.updateDB_skyIslandCoord('skyisland', 'tbl_sky_island_coordinate', int(i), k1, k2, p1, p2, p3)
    return 'COORDINATES UPDATE COMPLETE !'

if __name__ == '__main__':
    app.run()