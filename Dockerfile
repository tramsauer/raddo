FROM continuumio/miniconda3 AS builder
# FROM continuumio/miniconda3:4.9.2-alpine

# Install gdal
RUN conda install -c conda-forge gdal

# Install raddo
WORKDIR /app
COPY . .
RUN pip install .

ENTRYPOINT ["raddo"]
CMD [ "--help" ]

WORKDIR /data
