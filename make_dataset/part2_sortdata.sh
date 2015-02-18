#!/bin/bash

DIR=rpp2014v1/pdgLive/
if [ "$#" -eq 1 ]
then
  DIR=$1
fi
#echo $DIR

# Get Particle names
grep MASS $DIR/Particle.action* 2> /dev/null \
  | sed -n 's/.*\(\$.*\$\).*/\1/p' \
  | perl -p  -e 's/^\$// ; s/\$$// ; s/\$\s\$/\n/g' \
  | grep '^{{' \
  | sort \
  | uniq \
  > particle_names

function get_details {
  fgrep -h -A 5 $1 $DIR/Particle.action* \
    > particle_$1
}

function print_line {
  tag=td
  echo -n "$2:" >> all_details
  NUM=`grep -v ADDMIXTURE particle_$2 \
      | fgrep -v atomic  \
      | fgrep -v RATIO  \
      | fgrep -A 5 "$1" \
      | sed -n "/<$tag>/,/<\/$tag>/p" \
      | tr '\n' ' ' \
      | tr -s ' ' ' ' \
      | sed "s/<$tag>//" `
  echo $NUM >> all_details
}

function get_special_cases {
  echo WRITE THIS
}

get_details MASS
get_details LIFE
get_details WIDTH

echo > all_details
while read -r line;
do
  echo "$line" >> all_details
  print_line "$line" MASS
  print_line "$line" LIFE
  print_line "$line" WIDTH
done < particle_names
cat special_cases >> all_details


