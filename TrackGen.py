import sys, os

from pyogg import PyOggError, VorbisFile

application_path: str
if getattr(sys, "frozen", False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))


SCRIPT_HEADER: str = "/* Generated by TrackGen */\n\n"
ILLEGAL_CHARACTERS: list[str] = [" ", "-"]


class TrackGen:
    def __init__(self) -> None:
        self.trackScript: str = SCRIPT_HEADER

    def generateTrack(self, name: str, sound: str, duration: float) -> None:
        """
        Creates a script block with the passed data, and adds it to self.trackScript
        :param name: Name of the track
        :param sound: The sound script the track relates to
        :param duration: The duration of the sound in seconds
        :return:
        """
        self.trackScript += f"track {name} {{\n    sound = {sound},\n    duration = {duration},\n}}\n\n"

    def generateTracks(self, directories: list[str]) -> None:
        """
        Creates script blocks for all the files in filenames, and adds them to self.trackScript
        :param directories: List of filepaths to sound files. File extensions must be included, otherwise it will assume
        it is a folder and recursively search it for oggs.
        :return:
        """
        if len(directories) < 1:
            print("No files were provided")
            return

        filenames: list[str] = []
        for directory in directories:
            if "." in directory:
                filenames.append(directory)
            elif os.path.exists(directory):
                # TODO: way too much nesting here
                for _, _, files in os.walk(directory):
                    for file in files:
                        if file.endswith(".ogg"):
                            filenames.append(directory + "/" + file)
            else:
                print(f"Unrecognised path {directory}")

        numFiles: int = len(filenames)
        if numFiles < 1:
            print("No files were found")
            return

        skippedFiles: int = 0
        for filename in filenames:
            try:
                file = VorbisFile(filename)
            except PyOggError as e:
                print(f"Unable to open file {filename}, skipping")
                print(f"PyOgg Error: {e}")
                skippedFiles += 1
                continue
            # i don't know why dividing by two is needed, but it was accurate on all files tested
            duration = file.buffer_length / file.frequency / file.channels / 2

            trackName: str = filename.split("\\")[-1].split(".")[0]
            for char in ILLEGAL_CHARACTERS:
                trackName = trackName.replace(char, "")
            # TODO: can we generate a translations file from the metadata?
            # TODO: switch to disable the truemusicification
            self.generateTrack(trackName, f"Cassette{trackName}", duration)
            print(f"Processed {filename}")

        if skippedFiles > 0:
            print(f"Skipped {skippedFiles} of {numFiles} files")

    def writeFiles(self, filename: str) -> None:
        """
        Writes the trackScript to file
        :param filename: Filename to write to. Existing files will be overwritten.
        File extension should not be included. _tracks will be appended automatically
        :return:
        """
        filename = application_path + f"/{filename}_tracks.txt"
        try:
            file = open(filename, "w", encoding="utf-8")
        except OSError:
            print(f"ERROR: Could not open {filename} for editing")
            return

        print(f"Writing {filename}")
        file.write(self.trackScript)
        file.close()


if __name__ == '__main__':
    gen: TrackGen = TrackGen()
    gen.generateTracks(sys.argv[1:])
    # TODO: switch to change output name
    gen.writeFiles("TrackGen")
