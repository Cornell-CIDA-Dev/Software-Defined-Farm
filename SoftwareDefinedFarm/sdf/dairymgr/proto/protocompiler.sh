#!/bin/bash

protoc -I=. --python_out=. historical.proto
