FROM python:3.10.6-buster

ENV WORKING_DIR /user/app/TeTuePzChallengeBot
WORKDIR $WORKING_DIR

COPY requirements.txt ./

RUN pip install discord.py
RUN pip install pyyaml
RUN pip install Pillow

COPY files/ ./files/
COPY source/ ./source/

ENV PYTHONPATH "${PYTHONPATH}:/user/app/TeTuePzChallengeBot"

WORKDIR /user/app/TeTuePzChallengeBot/source/

CMD ["python", "-u", "main.py"]
