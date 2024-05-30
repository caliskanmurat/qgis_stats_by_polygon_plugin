# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:25:54 2024

@author: caliskan.murat
"""

from PIL import ImageDraw, Image
import numpy as np

class ZonalStatistics():
    def __init__(self, raster):        
        self.GEOT = raster.GetGeoTransform()
        self.BANDS = [raster.GetRasterBand(i) for i in range(1,raster.RasterCount+1)]
    
    def getVectorParams(self, geom):
        ext_points, hole_points = [], []
        minx,maxx,miny,maxy = geom.GetEnvelope()
        
        if geom.GetGeometryName() == "POLYGON":
            for e2, ring in enumerate(geom, 1):
                pnt_cnt = ring.GetPointCount()
                pnt_list = np.array([ring.GetPoint_2D(i) for i in range(pnt_cnt)])
                if e2 == 1:
                    ext_points.append(pnt_list)
                else:
                    hole_points.append(pnt_list)
        
        elif geom.GetGeometryName() == "MULTIPOLYGON":
            for e1, pol in enumerate(geom, 1):
                for e2, ring in enumerate(pol,1):
                    pnt_cnt = ring.GetPointCount()
                    pnt_list = np.array([ring.GetPoint_2D(i) for i in range(pnt_cnt)])
                    if e2 == 1:
                        ext_points.append(pnt_list)
                    else:
                        hole_points.append(pnt_list)
        
        return ext_points, hole_points, (minx,maxx,miny,maxy)
    
    def getArray(self, band, minx, maxx, miny, maxy):
        xoff = int((minx-self.GEOT[0])/self.GEOT[1])
        yoff = int((maxy-self.GEOT[3])/self.GEOT[5])
        xsize = int((maxx-minx)/self.GEOT[1])+1
        ysize = int((miny-maxy)/self.GEOT[5])+1
        
        new_geot = (
            self.GEOT[0] + (xoff * self.GEOT[1]), 
            self.GEOT[1],
            self.GEOT[2],
            self.GEOT[3] + (yoff * self.GEOT[5]),
            self.GEOT[4],
            self.GEOT[5]
            )
        
        arr = band.ReadAsArray(xoff, yoff, xsize, ysize)
        
        return arr, new_geot
        
    def getMaskedArrays(self, geom):
        result = []
        band_names = []
        
        ext_points, hole_points, (minx, maxx, miny, maxy) = self.getVectorParams(geom)
        
        for e, band in enumerate(self.BANDS, 1):
            arr, new_geot = self.getArray(band, minx, maxx, miny, maxy)
            nodatavalue = int(band.GetNoDataValue()) if band.GetNoDataValue() else int((arr.max()+10).copy())
            
            img = Image.fromarray(arr)                
            draw = ImageDraw.Draw(img)
            
            band_name = band.GetDescription() if band.GetDescription() else f"band_{e}"            
            band_names.append(band_name)
            
            for e,i in enumerate(ext_points):
                shp_col = ((i[:,0]-new_geot[0])/new_geot[1]).astype(int)
                shp_row = ((i[:,1]-new_geot[3])/new_geot[5]).astype(int)
    
                draw.polygon([(x,y) for x,y in zip(shp_col,shp_row)], fill=nodatavalue, outline=nodatavalue)
            
            img = np.where(np.array(img)==nodatavalue, arr, nodatavalue)        
            img = Image.fromarray(img)                
            draw = ImageDraw.Draw(img)
            
            for i in hole_points:
                shp_col = ((i[:,0]-new_geot[0])/new_geot[1]).astype(int)
                shp_row = ((i[:,1]-new_geot[3])/new_geot[5]).astype(int)
    
                draw.polygon([(x,y) for x,y in zip(shp_col,shp_row)], fill=nodatavalue, outline=nodatavalue)
            
            result.append(np.where(np.array(img) == nodatavalue, np.nan, np.array(img)))
        
        return band_names, result
    
    def run(self, geom_list):
        return [self.getMaskedArrays(geom) for geom in geom_list]

