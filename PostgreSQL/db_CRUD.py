from PostgreSQL.db_auth import Databases


class CRUD(Databases):
    def updateDB_skyIslandCoord(self, schema, table, skyIslandId, k1, k2, k3, k4, pc1, pc2, pc3):
        sql1 = f" UPDATE {schema}.{table} SET "
        sql2 = f"id={skyIslandId}, keyword1='{k1}', keyword2='{k2}', keyword3='{k3}', keyword4='{k4}', pc1={pc1}, pc2={pc2}, pc3={pc3} "
        sql3 = f"WHERE id = {skyIslandId}"
        sql = sql1 + sql2 + sql3
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(" update DB err", e)

    def readDB_all_tag(self):
        sql = """
            SELECT (sky.id, avttag.content)
            FROM skyisland.tbl_sky_island AS sky
                INNER JOIN avatar.tbl_avatar_tag AS avttag
                ON sky.avatar_id = avttag.avatar_id
        """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    def readDB_all_image_url(self):
        sql = """
            SELECT (sky.id, atc.saved_path)
            FROM skyisland.tbl_sky_island AS sky
                INNER JOIN avatar.tbl_avatar AS avt
                    ON sky.avatar_id = avt.id
                INNER JOIN file.tbl_atc AS atc
                    ON avt.image_id = atc.id
        """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result