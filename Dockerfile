FROM jupyter/scipy-notebook

WORKDIR /home/daniel/tcc

COPY ./src .

VOLUME [ "/src" ]

RUN pip install -r requeriments.txt

EXPOSE 8888

#ENTRYPOINT ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root"]

ENTRYPOINT ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--allow-root"]
