#!/bin/bash

protoc -I ../../stock_service --cpp_out=. stock_provider.proto
protoc -I ../../stock_service --grpc_out=. --plugin=protoc-gen-grpc=/usr/local/bin/grpc_cpp_plugin stock_provider.proto
