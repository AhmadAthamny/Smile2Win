class Participant:
    def __init__(self):
        self.__name = None
        self.__picture = None
        self.__faceId = None
        self.__points = 0

    def get_name(self):
        return self.__name

    def get_picture(self):
        return self.__picture

    def get_faceId(self):
        return self.__faceId

    def get_points(self):
        return self.__points

    def set_name(self, new_name):
        self.__name = new_name

    def set_picture(self, new_picture):
        self.__picture = new_picture

    def set_faceId(self, new_faceid):
        self.__faceId = new_faceid

    def set_points(self, new_points):
        self.__points = new_points

    def give_points(self, amount):
        self.set_points(self.get_points() + amount)


class ParticipantsList:
    def __init__(self):
        self.__participants_list = []
        self.__face_encodings = []

    def add_participant(self, name, faceid, image):
        new_p = Participant()
        new_p.set_picture(image)
        new_p.set_faceId(faceid)
        new_p.set_name(name)

        self.__participants_list.append(new_p)
        self.__face_encodings.append(faceid)

    def get_participant_from_name(self, name):
        for p in self.__participants_list:
            if p.get_name() == name:
                return p
        return None

    def get_participant_from_faceId(self, faceid):
        for p in self.__participants_list:
            if p.get_faceId() == faceid:
                return p
        return None

    def sort_by_points(self):
        self.__participants_list.sort(key=lambda e: e.get_points())

    def remove_participant(self, participant):
        try:
            p_index = self.__participants_list.index(participant)
            self.__participants_list.remove(participant)
            self.__face_encodings.pop(p_index)
        except:
            # participant not in list.
            pass

    def remove_all_participants(self):
        self.__participants_list = []
        self.__face_encodings = []

    def get_participants_count(self):
        return len(self.__participants_list)
    
    def get_participants_encodings(self):
        return self.__participants_list, self.__face_encodings
    
    def get_all_participants(self):
        return self.__participants_list