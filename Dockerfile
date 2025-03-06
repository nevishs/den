FROM python:3-alpine
ENV token=
RUN apk update && apk upgrade \
&& pip install pyYaml docker six
WORKDIR /app
COPY /app/* /app/
CMD ["python", "main.py"]