class Timer:
    def execTime(self, startT, endT):
        segundos = int(endT - startT)

        horas = int(segundos / 60 / 60)
        segundos -= horas*60*60
        minutos = int(segundos/60)
        segundos -= minutos*60
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"