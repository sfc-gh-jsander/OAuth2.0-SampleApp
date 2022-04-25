use database XXXX;
use schema XXXX;
use warehouse XXXX;
GET @test_named_stage/test.csv file:///XXXXXXX ;
!system gunzip test.csv.gz