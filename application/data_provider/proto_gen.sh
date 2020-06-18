#!/bin/bash

protoc -I ../../clients/grpc_converter --cpp_out=. stock_provider.proto
protoc -I ../../clients/grpc_converter --grpc_out=. --plugin=protoc-gen-grpc=/usr/local/bin/grpc_cpp_plugin stock_provider.proto
