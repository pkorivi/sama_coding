import json
from operator import truediv
from pickle import FALSE


class ValidateAnnotations:
    def __init__(self, file):
        self.total_errors = []
        self.errors = []
        self.triangles = 0
        with open('Question_1.json', 'r') as f:
            data = json.load(f)
            for annotation in data['tasks']:
                self.checkForErrorsInAnnotation(annotation)
                self.ValidateNumberOfTriangles()
                self.total_errors.append(self.errors)
                self.triangles = 0
                self.errors = []

            for i in range(len(self.total_errors)):
                print("Errors in Task {} : ".format(i))
                for error in self.total_errors[i]:
                    print("* ", error)
                print("-----")

    def IsShapeGroupAValidTriangle(self, shape_group):
        group_type = shape_group.get('group_type')
        shapes = shape_group.get('shapes')
        length = len(shapes)
        valid_triangle = False
        for shape in shapes:
            if ('Triangle' in shape.get('tags').values()):
                self.triangles = self.triangles + 1
                if ('Occlusion' not in shape.get('tags').keys()):
                    valid_triangle = True
                else:
                    self.errors.append("Occlusion in Triangle")

        if (valid_triangle and (length != 1 or group_type != None)):
            self.errors.append("Invalid Grouping of Triangle")

        return ((valid_triangle == True) and (length == 1) and (group_type == None))

    def areCornersClockwiseStartingTopLeft(self, corners):
        quad_starts_top_left = False
        quad_points_are_clockwise = False
        centroid = [(sum(corners[i][0] for i in range(len(corners))))/len(corners), (sum(
            corners[i][1] for i in range(len(corners))))/len(corners)]

        # To check if the Quad starts at top left
        if (corners[0][0] < centroid[0] and corners[0][1] > centroid[1]):
            quad_starts_top_left = True
        else:
            self.errors.append("Quad does not start top left")

        corners.append(corners[0])
        # if val is positive then points are clockwise
        val = sum(((corners[i+1][0]-corners[i][0])*(corners[i+1]
                                                    [1]+corners[i][1])) for i in range(0, len(corners)-1))
        if (val >= 0):
            quad_points_are_clockwise = True
        else:
            self.errors.append("Quad Points are not clockwise")

        return (quad_starts_top_left and quad_points_are_clockwise)

    def isQuadValid(self, shape):
        result = False
        corners = shape.get("key_locations")[0].get("points")
        if (len(corners) == 4):
            occlusion = False
            if ("Occlusion" in shape.get("tags")):
                occlusion = "1" in shape.get("tags").get("Occlusion").values()

            if (occlusion == False):
                result = self.areCornersClockwiseStartingTopLeft(corners)
            else:
                result = True

        else:
            self.errors.append(
                "Quad Contains {} number of corners".format(len(corners)))

        return result

    def isShapeGroupAValidQuadGroup(self, shape_group):
        result = False
        shapes = shape_group.get('shapes')
        length = len(shapes)
        valid_quad = False
        valid_point = False
        quad_count = 0
        point_count = 0
        for shape in shapes:
            if ('Quad' in shape.get('tags').values()):
                valid_quad = valid_quad or self.isQuadValid(shape)
                quad_count = quad_count+1
            if (shape.get('type') == "point"):
                point_count = point_count+1
                if ('Occlusion' not in shape.get('tags').keys()):
                    valid_point = True
                else:
                    self.errors.append("Occlusion in Point")

        if (length == 2 and valid_quad and valid_point and quad_count == 1 and point_count == 1):
            result = True

        if (length > 2 or quad_count > 1 or point_count > 1):
            self.errors.append(
                "Wrong number of Quads and Points are grouped together")

        return result

    def validate_shape_group(self,  shape_group):
        if (self.IsShapeGroupAValidTriangle(shape_group)):
            return
        elif (self.isShapeGroupAValidQuadGroup(shape_group)):
            return

    def ValidateNumberOfTriangles(self):
        if (self.triangles != 1):
            self.errors.append(
                "Invalid Count of Triangles : {}".format(self.triangles))

    def checkForErrorsInAnnotation(self,  annotation):
        shape_groups = annotation.get('answers').get('Annotation').get(
            'layers').get('vector_tagging').get('shape_groups')
        for shape_group in shape_groups:
            self.validate_shape_group(shape_group)


if __name__ == "__main__":
    va = ValidateAnnotations('Question_1.json')
